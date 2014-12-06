package tokenize;
require Exporter;
use strict;

our @ISA = qw(Exporter);
our @EXPORT = qw(tokenize read_pos_line);
our @EXPORT_OK = ();

sub read_pos_line
{
  my ($line) = @_;
  my @tokens;
  my @pos;

  # first, remove the misc. chunking information
  $line =~ s/\[\*//g;
  $line =~ s/\*\]//g;
  $line =~ s/\(\(//g;
  $line =~ s/\)\)//g;
  $line =~ s/<S>//g;
  $line =~ s/<\/S>//g;

  if( $line =~ /^\s*(\d+)\._CD\s+_\.$/ )
  {
    # this should be an LS
    $line = "$1_LS ._.";
  }

  my @pairs = split /\s+/, $line;

  # split out the pos and the words and add them to the list of tokens
  for my $pair (@pairs)
  {
    if( $pair )
    {
      if( $pair eq "_" )
      {
	push @tokens, $pair;
	push @pos, $pair;
      }
      else
      {
	my @vals = split /_/, $pair;

	if( scalar(@vals) < 2 )
	{
	  print STDERR "WARNING: Couldn't find part of speech in pair: $pair\n";
          push @tokens, $pair;
          push @pos, $pair;
	}
	else
        {	
	  my $word = "";
      
	  for( my $i = 0; $i < scalar(@vals)-1; $i++ )
	  {
	    if( $word )
	    {
	      $word .= "_";
	    }
	
	    $word .= $vals[$i];
	  }
	
	  push @tokens, $word;
	  push @pos, $vals[scalar(@vals)-1];
        }
      }
    }
  }

  return (\@tokens, \@pos);
}

sub tokenize
{
  my ($line) = @_;
  my @temp_tokens;

  while( $line )
  {
    # find the first white space or punctuation character
    if( $line =~ /([ \.,;:?\"\(\)\%\$])/ )
    {
      # figure out where this character actually occurred
      my $index = index $line, $1;

      if( $index > 0 )
      {
				# add this token
				push @temp_tokens, substr($line, 0, $index);
      }

      
      # add the punctuation character to the token list
      push @temp_tokens, $1;
      
      $line = substr($line, $index+1);
    }
    else
    {
      # we're done processing, just put the last token on
      push @temp_tokens, $line;
      $line = "";
    }
  }

  # now, put back together things like numbers and abreviations that should be kept together
  my @tokens;
  my $number = "";

  for( my $i = 0; $i < scalar(@temp_tokens); $i++ )
  {
    if( $temp_tokens[$i] =~ /^[\d]+$/ ||
		    ($temp_tokens[$i] =~ /^\w$/ && $number !~ /^[\d\.,]+$/) )
    {
      # don't add it yet
      $number .= $temp_tokens[$i];
    }
    elsif( ($temp_tokens[$i] eq "." ||
	    $temp_tokens[$i] eq ",") &&
	    $i != scalar(@temp_tokens)-1 &&
	    $temp_tokens[$i+1] =~ /^\d+$/ &&
	    $number =~ /\d$/ )
    {
      # add this on to the end of numbers
      $number .= $temp_tokens[$i];
    }
		elsif( $temp_tokens[$i] eq "." &&
					 $i > 0 &&
					 $temp_tokens[$i-1] =~ /^\w$/ )
		{
			$number .= $temp_tokens[$i];
		}
    else
    {
      # add number if there's anything there
      if( $number )
      {
				if( $number =~ /^(.*)([\.,])$/ )
				{
	  			push @tokens, $1;
	  			push @tokens, $2;
				}
				else
				{
	  			push @tokens, $number;
				}

				$number = "";
      }

      if( $temp_tokens[$i] !~ /^\s+$/ )
      {
				push @tokens, $temp_tokens[$i];
      }
    }
  }

  if( $number )
  {
    push @tokens, $number;
    
    $number = "";
  }

  return \@tokens;
}

1;
