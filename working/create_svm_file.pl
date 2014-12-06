#! /usr/bin/perl -w

#use lib '/Users/drk04747/resources';

use strict;
use tokenize;

&main();

sub main{
	if( scalar(@ARGV) != 2 ){
		&print_usage();
		exit 1;
	}

	my $data_file = $ARGV[0];
	my $stoplist = $ARGV[1];

	my $stop = &read_stoplist($stoplist);

	open IN, $data_file or die "Problems opening file: $data_file\n$!";
	open OUT, ">feature_list.txt";

	my %features;
	my $feature_count = 1;

	while( my $line = <IN> ){
		chomp $line;

		$line = lc($line);

		my ($label, $text) = split /\t/, $line;

		my $tokens = &tokenize::tokenize($text);
		my $counts = &get_word_counts($tokens);

		print $label;

		my %printme;

		for my $tok (keys(%{$counts})){
			if( !$stop->{$tok} ){
				if( !(exists $features{$tok}) ){
					$features{$tok} = $feature_count;
					print OUT "$feature_count\t$tok\n";
					$feature_count++;
				}

				$printme{$features{$tok}} = $counts->{$tok};
			}
		}

		for my $f_num (sort {$a <=> $b} keys(%printme)){
			print " " . $f_num . ":" . $printme{$f_num};
		}

		print "\n";
	}

	close IN;
	close OUT;
}

sub get_word_counts{
	my ($words) = @_;

	my %count;

	for my $w (@$words){
		$count{$w}++;
	}

	return \%count;
}

sub read_stoplist{
	my ($stop_file) = @_;

	open IN, $stop_file or die "Problems opening file: $stop_file\n$!";

	my %stop;

	while( my $line = <IN> ){
		chomp $line;

		$stop{$line} = 1;
	}

	return \%stop;
}

sub print_usage{
	print STDERR "create_svm_file.pl <data_file> <stoplist>\n";
}
